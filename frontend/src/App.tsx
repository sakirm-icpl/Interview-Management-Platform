import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

// Public pages
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/ResetPasswordPage';
import { VerifyEmailPage } from '@/pages/VerifyEmailPage';

// Protected pages
import { DashboardPage } from '@/pages/DashboardPage';
import { JobsPage } from '@/pages/JobsPage';
import { JobDetailPage } from '@/pages/JobDetailPage';
import { ApplicationsPage } from '@/pages/ApplicationsPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { InterviewsPage } from '@/pages/InterviewsPage';
import { ChatbotPage } from '@/pages/ChatbotPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { SettingsPage } from '@/pages/SettingsPage';

// HR specific pages
import { JobPostingPage } from '@/pages/JobPostingPage';
import { CandidatesPage } from '@/pages/CandidatesPage';
import { OffersPage } from '@/pages/OffersPage';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/dashboard" />} />
      <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to="/dashboard" />} />
      <Route path="/forgot-password" element={!user ? <ForgotPasswordPage /> : <Navigate to="/dashboard" />} />
      <Route path="/reset-password" element={!user ? <ResetPasswordPage /> : <Navigate to="/dashboard" />} />
      <Route path="/verify-email" element={!user ? <VerifyEmailPage /> : <Navigate to="/dashboard" />} />
      
      {/* Protected routes */}
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="jobs" element={<JobsPage />} />
        <Route path="jobs/:id" element={<JobDetailPage />} />
        <Route path="applications" element={<ApplicationsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="interviews" element={<InterviewsPage />} />
        <Route path="chatbot" element={<ChatbotPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="settings" element={<SettingsPage />} />
        
        {/* HR specific routes */}
        <Route path="post-job" element={<JobPostingPage />} />
        <Route path="candidates" element={<CandidatesPage />} />
        <Route path="offers" element={<OffersPage />} />
      </Route>
      
      {/* 404 route */}
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

export default App;