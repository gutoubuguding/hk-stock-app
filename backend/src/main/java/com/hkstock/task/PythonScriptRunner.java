package com.hkstock.task;

import com.hkstock.exception.DataSyncException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Shared Python script runner for scheduled sync tasks.
 *
 * <p>Task classes only describe scheduling intent. Script path resolution, process lifecycle,
 * stdout/stderr logging, timeout handling and retry behavior are centralized here.
 */
@Component
public class PythonScriptRunner {

  private static final Logger log = LoggerFactory.getLogger(PythonScriptRunner.class);
  private static final int MAX_RETRY = 1;

  @Value("${app.python.executable:python}")
  private String pythonExe;

  @Value("${app.scripts.root:..}")
  private String scriptRoot;

  public void run(String scriptName, String taskName) {
    run(scriptName, taskName, resolveTimeoutMinutes(scriptName));
  }

  public void run(String scriptName, String taskName, long timeoutMinutes) {
    String scriptPath = resolveScript(scriptName);
    DataSyncException lastError = null;

    for (int attempt = 1; attempt <= MAX_RETRY + 1; attempt++) {
      try {
        doRun(scriptPath, taskName, timeoutMinutes, attempt);
        return;
      } catch (DataSyncException e) {
        lastError = e;
        if (attempt <= MAX_RETRY) {
          log.warn("[{}] Failed, retrying attempt {}: {}", taskName, attempt, e.getMessage());
        }
      }
    }

    throw lastError;
  }

  private void doRun(String scriptPath, String taskName, long timeoutMinutes, int attempt) {
    long startTime = System.currentTimeMillis();
    log.info("[{}] Starting Python script, attempt {}, script: {}", taskName, attempt, scriptPath);

    try {
      ProcessBuilder pb = new ProcessBuilder(pythonExe, scriptPath);
      pb.redirectErrorStream(false);

      Process process = pb.start();
      Thread stdoutReader = streamToLog(process, taskName, false);
      Thread stderrReader = streamToLog(process, taskName, true);

      boolean finished = process.waitFor(timeoutMinutes, TimeUnit.MINUTES);
      if (!finished) {
        process.destroyForcibly();
        throw new DataSyncException("Script timed out after " + timeoutMinutes + " minute(s)");
      }

      joinQuietly(stdoutReader);
      joinQuietly(stderrReader);

      int exitCode = process.exitValue();
      long elapsedSeconds = (System.currentTimeMillis() - startTime) / 1000;
      if (exitCode != 0) {
        throw new DataSyncException(
            "Script exited with code " + exitCode + ", elapsed seconds: " + elapsedSeconds);
      }

      log.info("[{}] Completed, elapsed seconds: {}", taskName, elapsedSeconds);
    } catch (DataSyncException e) {
      throw e;
    } catch (Exception e) {
      throw new DataSyncException("Script execution failed: " + e.getMessage(), e);
    }
  }

  private Thread streamToLog(Process process, String taskName, boolean errorStream) {
    Thread readerThread =
        new Thread(
            () -> {
              try (BufferedReader reader =
                  new BufferedReader(
                      new InputStreamReader(
                          errorStream ? process.getErrorStream() : process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                  if (errorStream) {
                    log.warn("[{}] stderr: {}", taskName, line);
                  } else {
                    log.info("[{}] {}", taskName, line);
                  }
                }
              } catch (Exception e) {
                log.warn("[{}] Failed to read {}", taskName, errorStream ? "stderr" : "stdout", e);
              }
            },
            taskName + (errorStream ? "-stderr" : "-stdout"));
    readerThread.start();
    return readerThread;
  }

  private void joinQuietly(Thread thread) {
    try {
      thread.join(TimeUnit.SECONDS.toMillis(5));
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
    }
  }

  private String resolveScript(String scriptName) {
    return Path.of(scriptRoot, scriptName).toString();
  }

  private long resolveTimeoutMinutes(String scriptName) {
    return scriptName.contains("kline") ? 60 : 10;
  }
}
