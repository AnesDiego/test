// Firebase Configuration
import { initializeApp } from 'firebase/app';
import { getAuth, sendSignInLinkToEmail, isSignInWithEmailLink, signInWithEmailLink, onAuthStateChanged, signOut } from 'firebase/auth';
import { getFirestore, collection, addDoc, query, where, orderBy, limit, getDocs } from 'firebase/firestore';

const firebaseConfig = {
    // Adicione suas configurações do Firebase aqui
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "your-app-id"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Magic Link Authentication
class MagicLinkAuth {
    constructor() {
        this.auth = auth;
        this.db = db;
        this.init();
    }

    init() {
        // Check if user is returning from email link
        if (isSignInWithEmailLink(this.auth, window.location.href)) {
            this.completeSignIn();
        }

        // Monitor auth state
        onAuthStateChanged(this.auth, (user) => {
            this.updateUI(user);
        });
    }

    async sendMagicLink(email) {
        const actionCodeSettings = {
            url: window.location.origin + '/auth/complete',
            handleCodeInApp: true,
        };

        try {
            await sendSignInLinkToEmail(this.auth, email, actionCodeSettings);
            localStorage.setItem('emailForSignIn', email);
            return { success: true, message: 'Magic link sent to your email!' };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async completeSignIn() {
        let email = localStorage.getItem('emailForSignIn');
        if (!email) {
            email = window.prompt('Please provide your email for confirmation');
        }

        try {
            const result = await signInWithEmailLink(this.auth, email, window.location.href);
            localStorage.removeItem('emailForSignIn');
            return { success: true, user: result.user };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    async logout() {
        try {
            await signOut(this.auth);
            return { success: true };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    updateUI(user) {
        const loginBtn = document.getElementById('loginBtn');
        const userMenu = document.getElementById('userMenu');
        const userName = document.getElementById('userName');

        if (user) {
            if (loginBtn) loginBtn.style.display = 'none';
            if (userMenu) userMenu.style.display = 'block';
            if (userName) userName.textContent = user.email;
        } else {
            if (loginBtn) loginBtn.style.display = 'block';
            if (userMenu) userMenu.style.display = 'none';
        }
    }

    async saveAnalysis(ipAddress, analysisData) {
        if (this.auth.currentUser) {
            try {
                await addDoc(collection(this.db, 'analyses'), {
                    userId: this.auth.currentUser.uid,
                    userEmail: this.auth.currentUser.email,
                    ipAddress: ipAddress,
                    analysisData: analysisData,
                    timestamp: new Date()
                });
                return { success: true };
            } catch (error) {
                console.error('Error saving analysis:', error);
                return { success: false, message: error.message };
            }
        }
        return { success: false, message: 'User not authenticated' };
    }

    async getUserHistory(limitCount = 20) {
        if (this.auth.currentUser) {
            try {
                const q = query(
                    collection(this.db, 'analyses'),
                    where('userId', '==', this.auth.currentUser.uid),
                    orderBy('timestamp', 'desc'),
                    limit(limitCount)
                );
                
                const querySnapshot = await getDocs(q);
                const history = [];
                querySnapshot.forEach((doc) => {
                    history.push({ id: doc.id, ...doc.data() });
                });
                
                return { success: true, data: history };
            } catch (error) {
                console.error('Error fetching history:', error);
                return { success: false, message: error.message };
            }
        }
        return { success: false, message: 'User not authenticated' };
    }
}

// Speed Test Implementation
class SpeedTest {
    constructor() {
        this.testServers = [
            'https://httpbin.org/bytes/1000000',  // 1MB
            'https://jsonplaceholder.typicode.com/photos',
            'https://api.github.com/users/octocat'
        ];
    }

    async measureLatency(url) {
        const start = performance.now();
        try {
            await fetch(url, { method: 'HEAD', mode: 'no-cors' });
            return performance.now() - start;
        } catch (error) {
            return null;
        }
    }

    async measureDownloadSpeed() {
        const testUrl = 'https://httpbin.org/bytes/1000000'; // 1MB test file
        const start = performance.now();
        
        try {
            const response = await fetch(testUrl);
            const data = await response.blob();
            const end = performance.now();
            
            const duration = (end - start) / 1000; // Convert to seconds
            const sizeInBits = data.size * 8; // Convert bytes to bits
            const speedMbps = (sizeInBits / duration) / (1024 * 1024); // Convert to Mbps
            
            return {
                success: true,
                downloadMbps: Math.round(speedMbps * 100) / 100,
                latencyMs: Math.round(end - start),
                testSize: data.size
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async measureUploadSpeed() {
        // Simulated upload test (posting data)
        const testData = new Blob([new ArrayBuffer(100000)]); // 100KB
        const start = performance.now();
        
        try {
            const formData = new FormData();
            formData.append('file', testData);
            
            await fetch('https://httpbin.org/post', {
                method: 'POST',
                body: formData
            });
            
            const end = performance.now();
            const duration = (end - start) / 1000;
            const sizeInBits = testData.size * 8;
            const speedMbps = (sizeInBits / duration) / (1024 * 1024);
            
            return {
                success: true,
                uploadMbps: Math.round(speedMbps * 100) / 100,
                testSize: testData.size
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async runFullSpeedTest() {
        const results = {
            timestamp: new Date().toISOString(),
            tests: {}
        };

        // Test latency to multiple servers
        const latencyTests = await Promise.all(
            this.testServers.map(url => this.measureLatency(url))
        );
        
        const validLatencies = latencyTests.filter(l => l !== null);
        results.tests.latency = validLatencies.length > 0 ? 
            Math.round(validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length) : null;

        // Test download speed
        const downloadTest = await this.measureDownloadSpeed();
        results.tests.download = downloadTest;

        // Test upload speed
        const uploadTest = await this.measureUploadSpeed();
        results.tests.upload = uploadTest;

        return results;
    }
}

// Global instances
const magicAuth = new MagicLinkAuth();
const speedTest = new SpeedTest();

// Global functions for HTML
window.magicAuth = magicAuth;
window.speedTest = speedTest;

// Speed test function for button
window.runSpeedTest = async function() {
    const btn = event.target;
    const results = document.getElementById('speedTestResults');
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running Speed Test...';
    
    try {
        const testResults = await speedTest.runFullSpeedTest();
        
        if (testResults.tests.download.success) {
            results.innerHTML = `
                <div class="speed-test-results mt-3">
                    <div class="alert alert-success">
                        <h6><i class="fas fa-download"></i> Download Speed: ${testResults.tests.download.downloadMbps} Mbps</h6>
                        <h6><i class="fas fa-upload"></i> Upload Speed: ${testResults.tests.upload.success ? testResults.tests.upload.uploadMbps : 'N/A'} Mbps</h6>
                        <h6><i class="fas fa-stopwatch"></i> Latency: ${testResults.tests.latency || 'N/A'} ms</h6>
                        <small>Test completed at ${new Date().toLocaleTimeString()}</small>
                    </div>
                </div>
            `;
        } else {
            results.innerHTML = '<div class="alert alert-warning mt-3">Speed test failed. Please try again.</div>';
        }
        results.style.display = 'block';
    } catch (error) {
        results.innerHTML = '<div class="alert alert-danger mt-3">Speed test error: ' + error.message + '</div>';
        results.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-rocket"></i> Run Real Speed Test';
    }
};

// Magic link login function
window.sendMagicLink = async function() {
    const email = document.getElementById('emailInput').value;
    if (!email) {
        alert('Please enter your email address');
        return;
    }

    const result = await magicAuth.sendMagicLink(email);
    if (result.success) {
        alert('Magic link sent! Check your email and click the link to sign in.');
    } else {
        alert('Error: ' + result.message);
    }
};

// Logout function
window.logout = async function() {
    const result = await magicAuth.logout();
    if (result.success) {
        window.location.reload();
    }
};

export { magicAuth, speedTest };