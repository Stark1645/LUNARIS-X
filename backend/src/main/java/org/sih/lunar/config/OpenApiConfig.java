package org.sih.lunar.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("LUNARIS-X (SIH26166) Lunar Image Registration Engine API")
                        .version("1.0.0")
                        .description("Enterprise REST API for Automatic Sub-Pixel Registration of Chandrayaan-2 TMC-2 / OHRC and Lunar Reference Imagery.")
                        .contact(new Contact()
                                .name("SIH 2026 Core Engineering Team")
                                .email("team@sih2026.isro.gov.in"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0.html")));
    }
}
