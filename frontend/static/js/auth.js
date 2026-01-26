// Authentication Module for Wunderlists
import {
  auth,
  db,
  googleProvider,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  doc,
  setDoc,
  getDoc,
  serverTimestamp
} from './firebase-config.js';

// Current user state
let currentUser = null;

// Initialize auth state listener
export function initAuth(onUserLoggedIn, onUserLoggedOut) {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      currentUser = user;
      // Ensure user document exists in Firestore
      await ensureUserDocument(user);
      if (onUserLoggedIn) onUserLoggedIn(user);
    } else {
      currentUser = null;
      if (onUserLoggedOut) onUserLoggedOut();
    }
  });
}

// Create user document in Firestore if it doesn't exist
async function ensureUserDocument(user) {
  const userRef = doc(db, 'users', user.uid);
  const userSnap = await getDoc(userRef);

  if (!userSnap.exists()) {
    await setDoc(userRef, {
      email: user.email,
      displayName: user.displayName || user.email.split('@')[0],
      createdAt: serverTimestamp(),
      settings: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    });
  }
}

// Sign in with email and password
export async function loginWithEmail(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return { success: true, user: userCredential.user };
  } catch (error) {
    return { success: false, error: getErrorMessage(error.code) };
  }
}

// Create account with email and password
export async function signupWithEmail(email, password, displayName) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    // Create user document with display name
    await setDoc(doc(db, 'users', userCredential.user.uid), {
      email: email,
      displayName: displayName || email.split('@')[0],
      createdAt: serverTimestamp(),
      settings: {
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
      }
    });
    return { success: true, user: userCredential.user };
  } catch (error) {
    return { success: false, error: getErrorMessage(error.code) };
  }
}

// Sign in with Google
export async function loginWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return { success: true, user: result.user };
  } catch (error) {
    return { success: false, error: getErrorMessage(error.code) };
  }
}

// Sign out
export async function logout() {
  try {
    await signOut(auth);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// Get current user
export function getCurrentUser() {
  return currentUser;
}

// Get current user ID
export function getCurrentUserId() {
  return currentUser ? currentUser.uid : null;
}

// Convert Firebase error codes to user-friendly messages
function getErrorMessage(errorCode) {
  const errorMessages = {
    'auth/email-already-in-use': 'This email is already registered. Please sign in instead.',
    'auth/invalid-email': 'Please enter a valid email address.',
    'auth/operation-not-allowed': 'Email/password accounts are not enabled.',
    'auth/weak-password': 'Password should be at least 6 characters.',
    'auth/user-disabled': 'This account has been disabled.',
    'auth/user-not-found': 'No account found with this email.',
    'auth/wrong-password': 'Incorrect password. Please try again.',
    'auth/invalid-credential': 'Invalid email or password.',
    'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
    'auth/popup-closed-by-user': 'Sign-in popup was closed before completing.',
    'auth/cancelled-popup-request': 'Sign-in was cancelled.',
    'auth/popup-blocked': 'Sign-in popup was blocked by the browser.'
  };

  return errorMessages[errorCode] || 'An error occurred. Please try again.';
}
