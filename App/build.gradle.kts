// Root build.gradle.kts (Project level)

plugins {
    // 1. UPDATE KOTLIN VERSION to 2.2.21 (Latest available stable version in search)
    id("com.android.application") version "8.5.0" apply false
    id("com.android.library") version "8.5.0" apply false
    
    // 2. Make sure you are using a modern Kotlin version here
    id("org.jetbrains.kotlin.android") version "2.2.21" apply false 

    // If you are using Kotlin 2.0+ (like 2.2.21), this is how you declare the Compose Compiler Plugin.
    // The version should match the Kotlin version if you are using the new compiler plugin approach.
    id("org.jetbrains.kotlin.plugin.compose") version "2.2.21" apply false 
}
//... other configurations
android {
    namespace = "com.techtedapps.geminichat"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.techtedapps.geminichat"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
//<<<<<<< feature-gemini-app-enhancements
        val geminiApiKey = project.properties["geminiApiKey"] ?: "YOUR_API_KEY"
        buildConfigField("String", "GEMINI_API_KEY", "\"$geminiApiKey\"")
//=======
//>>>>>>> main
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.1")
    implementation("androidx.activity:activity-compose:1.7.2")
    implementation(platform("androidx.compose:compose-bom:2023.03.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("com.google.ai.client:generativeai:0.9.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.1")
    implementation("androidx.navigation:navigation-compose:2.7.7")
}
