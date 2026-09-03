package org.sih.lunar.exception;

public class PythonServiceUnavailableException extends RuntimeException {
    public PythonServiceUnavailableException(String message) {
        super(message);
    }

    public PythonServiceUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
