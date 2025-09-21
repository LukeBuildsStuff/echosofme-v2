import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/SupabaseAuthContext'
import { EchoProvider } from './contexts/EchoContext'
import { SettingsProvider } from './contexts/SettingsContext'
import { ToastProvider } from './contexts/ToastContext'
import { EleanorNotificationProvider, useEleanorNotification } from './contexts/EleanorNotificationContext'
import ErrorBoundary from './components/ErrorBoundary'
import EleanorNotification from './components/EleanorNotification'
import Home from './pages/Home'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import EnhancedReflections from './pages/EnhancedReflections'
import Legacy from './pages/Legacy'
import Insights from './pages/Insights'
import Settings from './pages/Settings'
import VoiceClone from './pages/VoiceClone'
import ResetPassword from './pages/ResetPassword'
import DatabaseAdmin from './pages/admin/DatabaseAdmin'

// Protected Route wrapper component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function AppRoutesWithNotifications() {
  const { currentNotification, dismissNotification } = useEleanorNotification();
  const navigate = useNavigate();

  const handleNotificationClick = () => {
    const message = currentNotification?.message;
    dismissNotification();
    // Pass Eleanor's message to the chat
    navigate('/chat', { state: { eleanorMessage: message } });
  };

  return (
    <>
      {currentNotification && (
        <EleanorNotification
          message={currentNotification.message}
          onDismiss={dismissNotification}
          onClick={handleNotificationClick}
        />
      )}
      <AppRoutes />
    </>
  );
}

function AppRoutes() {
  return (
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        
        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reflections"
          element={
            <ProtectedRoute>
              <EnhancedReflections />
            </ProtectedRoute>
          }
        />
        <Route
          path="/legacy"
          element={
            <ProtectedRoute>
              <Legacy />
            </ProtectedRoute>
          }
        />
        <Route
          path="/insights"
          element={
            <ProtectedRoute>
              <Insights />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/voice-clone"
          element={
            <ProtectedRoute>
              <VoiceClone />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/database"
          element={
            <ProtectedRoute>
              <DatabaseAdmin />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <SettingsProvider>
            <EchoProvider>
              <EleanorNotificationProvider>
                <Router>
                  <AppRoutesWithNotifications />
                </Router>
              </EleanorNotificationProvider>
            </EchoProvider>
          </SettingsProvider>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App