plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
}
rootProject.name = "Projeto-Final"

include("app")
include("domain")
include("docs")
include("http")
include("service")
include("repo")


include("untitled")
include("repo-jdbc")
include("scrapper")