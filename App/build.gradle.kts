plugins {
    // CRITICAL FIX: Explicitly applying the Android Application and Kotlin plugins 
    // to resolve 'android { ... }' and 'implementation' calls.
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.techtedapps.geminichat"
    compileSdk = 36 
    
    defaultConfig {
        applicationId = "com.techtedapps.geminichat"
        minSdk = 24
        targetSdk = 36 
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        // Properly retrieve the project property for the Build Config Field
        val geminiApiKey: String by project
        buildConfigField("String", "GEMINI_API_KEY", "\"$geminiApiKey\"")
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
        kotlinCompilerExtensionVersion = "2.0.21" 
    }

    packaging {
        resources {
            // Correct Kotlin DSL syntax for excluding files
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    
    val composeBom = platform("androidx.compose:compose-bom:2025.08.00") 
    implementation(composeBom)
    
    // Generative AI SDK
    implementation("com.google.ai.client:generativeai:0.9.0")
    
    // AndroidX and Compose dependencies
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.9.0")
    
    // Compose UI
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    
    // ViewModels and Navigation
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.navigation:navigation-compose:2.7.7")

    // Test dependencies
    testImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}