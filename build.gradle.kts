// Root build.gradle.kts (Project level)

plugins {
    // Updated Android Gradle Plugin (AGP) to a recommended stable version
    id("com.android.application") version "8.6.1" apply false
    id("com.android.library") version "8.6.1" apply false
    
    // Kotlin Gradle Plugin (KGP) - using the latest stable 2.2.21
    id("org.jetbrains.kotlin.android") version "2.2.21" apply false 

    // Compose Compiler Plugin using the new KGP 2.0+ approach
    id("org.jetbrains.kotlin.plugin.compose") version "2.2.21" apply false 
}