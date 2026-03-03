import React from 'react';
import { Bell, LogOut } from 'lucide-react';
import { Company } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

interface HeaderProps {
    company?: Company;
}

export const Header: React.FC<HeaderProps> = ({ company }) => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <header className="sticky top-0 z-50 w-full" style={{ background: 'rgba(248, 247, 244, 0.88)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(26, 26, 46, 0.06)' }}>
            <div className="max-w-[1400px] mx-auto flex h-16 items-center justify-between px-6 lg:px-12">
                <Link to="/app" className="flex items-center gap-1">
                    <span className="text-lg font-semibold tracking-tight" style={{ color: '#1a1a2e' }}>
                        HarborGuard<span style={{ color: '#c4a24e' }}>.</span>
                    </span>
                </Link>

                <div className="flex items-center space-x-5">
                    {company && (
                        <span className="text-xs tracking-widest uppercase" style={{ color: '#8a8a96' }}>
                            {company.name}
                        </span>
                    )}
                    <button className="relative p-2 transition-colors rounded-full hover:bg-black/5" style={{ color: '#8a8a96' }}>
                        <Bell className="h-4 w-4" />
                        <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full" style={{ background: '#c4a24e' }}></span>
                    </button>
                    <div className="h-5 w-px" style={{ background: 'rgba(26, 26, 46, 0.08)' }} />
                    <button
                        onClick={handleLogout}
                        className="flex items-center text-xs tracking-widest uppercase transition-colors hover:opacity-70"
                        style={{ color: '#8a8a96' }}
                    >
                        <LogOut className="h-3.5 w-3.5 mr-1.5" />
                        Logout
                    </button>
                </div>
            </div>
        </header>
    );
};
