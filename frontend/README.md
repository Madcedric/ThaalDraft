# ThaalDraft - Frontend

This is the Next.js client web application for **ThaalDraft**. It provides a premium, responsive dashboard for uploading manuscripts and converting them to compliant journal formats (like IEEE).

For full project architecture and authentication details, refer to the [Root README](file:///d:/hakathonProjks/New%20folder/README.md).

---

## 🛠️ Setup & Local Development

### 1. Environment Configuration

Create a `.env.local` file in this directory and populate it with your Firebase Web App credentials:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

_Note: During build processes and prerendering, if these environment variables are absent, the application automatically falls back to dummy configurations to avoid build-time errors._

### 2. Install Dependencies

```bash
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

---

## 🔒 Authentication Flow

The frontend integrates directly with **Firebase Auth** via client-side libraries.

- The `AuthProvider` context in [auth-context.tsx](file:///d:/hakathonProjks/New%20folder/frontend/lib/auth-context.tsx) intercepts authentication changes.
- Route protecting guards automatically redirect unauthenticated users away from `/dashboard` and logged-in users away from `/login`.
- Authenticated requests to the backend format API include the user's Firebase ID Token as a Bearer token in the `Authorization` header.
