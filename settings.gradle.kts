// settings.gradle
pluginManagement {
    repositories {
        gradlePluginPortal()
        google() // <-- THIS IS CRITICAL
        mavenCentral()
    }
}

include(":App")

dependencyResolutionManagement {
    // Defines repositories for the libraries/dependencies used by the modules
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "Gemini-App-No-Safety-API"