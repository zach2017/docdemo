package com.example.javaworker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class JavaWorkerApplication {
    public static void main(String[] args) {
        SpringApplication.run(JavaWorkerApplication.class, args);
    }
}
