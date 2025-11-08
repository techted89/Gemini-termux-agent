pluginManagement {
    // This block tells Gradle where to look for the plugins themselves (like com.android.application)
    repositories {
        // Android and Google services plugins are hosted here
        google()
        // Other common plugins and libraries are here
        mavenCentral()
        // Gradle's own portal for plugins
        gradlePluginPortal()
    }
}

// This section defines which modules are part of the project.
include(":App")

// Define repositories for dependencies (libraries used by the modules)
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "Gemini-App-No-Safety-API"