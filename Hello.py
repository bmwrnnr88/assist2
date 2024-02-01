// main.js (Vue 3 with Firebase Authentication for Google login)
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, onAuthStateChanged } from 'firebase/auth';

const firebaseConfig = {
    // Your Firebase configuration
};

initializeApp(firebaseConfig);

const auth = getAuth();
auth.languageCode = 'en';

let app;

onAuthStateChanged(auth, (user) => {
    if (!app) {
        app = createApp(App)
            .use(router)
            .mount('#app');
    }
});

export { auth, GoogleAuthProvider };