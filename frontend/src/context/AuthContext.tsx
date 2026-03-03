import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/endpoints';

interface AuthContextType {
    isAuthenticated: boolean;
    requiresMfa: boolean;
    mfaEmail: string | null;
    isLoading: boolean;
    loginStep1: (password: string, email?: string) => Promise<void>;
    loginStep2: (totpCode: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [requiresMfa, setRequiresMfa] = useState(false);
    const [mfaEmail, setMfaEmail] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check if we already have a valid token on mount
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
        }
        setIsLoading(false);
    }, []);

    const loginStep1 = async (password: string, email: string = "vp@harborguard.ai") => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        try {
            const response = await api.auth.login(params);
            if (response.requires_mfa) {
                // User needs to enter Google Authenticator code
                setRequiresMfa(true);
                setMfaEmail(email);
                setIsAuthenticated(false);
            } else {
                // Legacy or dev user without MFA
                localStorage.setItem('token', response.access_token);
                setIsAuthenticated(true);
                setRequiresMfa(false);
            }
        } catch (error) {
            console.error("Login Step 1 failed", error);
            throw new Error("Invalid credentials");
        }
    };

    const loginStep2 = async (totpCode: string) => {
        if (!mfaEmail) throw new Error("No MFA email context found");

        try {
            const response = await api.auth.verifyMfa(mfaEmail, totpCode);
            // Fully authenticated!
            localStorage.setItem('token', response.access_token);
            setIsAuthenticated(true);
            setRequiresMfa(false);
            setMfaEmail(null);
        } catch (error) {
            console.error("MFA Verify failed", error);
            throw new Error("Invalid Authenticator Code");
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setRequiresMfa(false);
        setMfaEmail(null);
    };

    return (
        <AuthContext.Provider value={{
            isAuthenticated,
            requiresMfa,
            mfaEmail,
            isLoading,
            loginStep1,
            loginStep2,
            logout
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
