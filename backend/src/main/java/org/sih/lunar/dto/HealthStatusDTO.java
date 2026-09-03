package org.sih.lunar.dto;

import java.util.List;

public class HealthStatusDTO {
    private String status; // UP | DOWN
    private String backendVersion;
    private String pythonServiceStatus;
    private String pythonServiceUrl;
    private String databaseStatus;
    private List<String> supportedAlgorithms;

    public HealthStatusDTO() {}

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getBackendVersion() { return backendVersion; }
    public void setBackendVersion(String backendVersion) { this.backendVersion = backendVersion; }

    public String getPythonServiceStatus() { return pythonServiceStatus; }
    public void setPythonServiceStatus(String pythonServiceStatus) { this.pythonServiceStatus = pythonServiceStatus; }

    public String getPythonServiceUrl() { return pythonServiceUrl; }
    public void setPythonServiceUrl(String pythonServiceUrl) { this.pythonServiceUrl = pythonServiceUrl; }

    public String getDatabaseStatus() { return databaseStatus; }
    public void setDatabaseStatus(String databaseStatus) { this.databaseStatus = databaseStatus; }

    public List<String> getSupportedAlgorithms() { return supportedAlgorithms; }
    public void setSupportedAlgorithms(List<String> supportedAlgorithms) { this.supportedAlgorithms = supportedAlgorithms; }
}
