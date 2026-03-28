plugins {
    kotlin("jvm") version "2.1.10"
    kotlin("plugin.spring") version "2.1.10"
    id("org.springframework.boot") version "3.5.6"
    id("io.spring.dependency-management") version "1.1.7"
    id("org.jlleitschuh.gradle.ktlint") version "12.1.1"
}

group = "pt.isel.ps"
version = "0.1.0-SNAPSHOT"

repositories {
    mavenCentral()
}


dependencies {
    api(project(":http"))
    implementation(project(":repo"))//repo-jdbc

    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-reflect")

    // for JDBI and Postgres
    implementation("org.jdbi:jdbi3-core:3.37.1")
    implementation("org.postgresql:postgresql:42.7.2")

    // To use WebTestClient in integration tests with real HTTP server
    testImplementation("org.springframework.boot:spring-boot-starter-webflux")

    // To automatically run the Spring MVC web server in coordination with unit tests
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.bootRun {
    environment("DB_URL", "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=iselPs123")
}

tasks.test {
    useJUnitPlatform()
    environment("DB_URL", "jdbc:postgresql://localhost:5432/postgres?user=postgres&password=iselPs123")
}

kotlin {
    jvmToolchain(21)
}

/**
 * Docker related tasks
 */
val dockerImageJvm = "odstool-jvm"
val dockerImagePostgres = "odstool-postgres"
val dockerImageUbuntu = "odstool-ubuntu"
val dockerImageNginx = "app-odstool-nginx"
val dockerExe =
    when (
        org.gradle.internal.os.OperatingSystem
            .current()
    ) {
        org.gradle.internal.os.OperatingSystem.MAC_OS -> "/usr/local/bin/docker"
        org.gradle.internal.os.OperatingSystem.WINDOWS -> "docker"
        else -> "docker" // Linux and others
    }

tasks.register<Copy>("extractUberJar") {
    dependsOn("assemble")
    // opens the JAR containing everything...
    from(
        zipTree(
            layout.buildDirectory
                .file("libs/app-$version.jar")
                .get()
                .toString(),
        ),
    )
    // ... into the 'build/dependency' folder
    into("build/dependency")
}

tasks.register<Exec>("buildImageJvm") {
    dependsOn("extractUberJar")
    commandLine(dockerExe, "build", "-t", dockerImageJvm, "-f", "docker/Dockerfile-jvm", ".")
}

tasks.register<Exec>("buildImagePostgres") {
    commandLine(
        dockerExe,
        "build",
        "-t", // Flag to assign a tag to the image
        dockerImagePostgres, // Name:tag of the image to be built (e.g., "my-postgres:test")
        "-f", // Flag to specify a custom Dockerfile
        "docker/Dockerfile-postgres", // Path to the Dockerfile used to build the image
        "../repo-jdbc", // Build context directory containing files referenced by the Dockerfile
    )
}

tasks.register<Exec>("buildImageUbuntu") {
    commandLine(dockerExe, "build", "-t", dockerImageUbuntu, "-f", "docker/Dockerfile-ubuntu", ".")
}

tasks.register("buildImageAll") {
    dependsOn("buildImageJvm")
    dependsOn("buildImagePostgres")
    dependsOn("buildImageUbuntu")
}

tasks.register<Exec>("allUp") {
    dependsOn("buildImageAll")
    commandLine(dockerExe, "compose", "up", "--force-recreate", "-d")
}

tasks.register<Exec>("allDown") {
    commandLine(dockerExe, "compose", "down")
}

tasks.register<Exec>("cleanImages") {
    dependsOn("allDown")
    commandLine(dockerExe, "rmi", "-f", dockerImageJvm, dockerImagePostgres, dockerImageUbuntu, dockerImageNginx)
}

tasks.register("cleanBuildAll") {
    dependsOn("cleanImages")
    dependsOn("clean")
    dependsOn("build")
    dependsOn("allUp")
}
