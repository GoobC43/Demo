import React, { ReactNode } from 'react';
import { Header } from './Header';
import { Company } from '../../types';

interface AppLayoutProps {
    children: ReactNode;
    company?: Company;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children, company }) => {
    return (
        <div className="min-h-screen flex flex-col font-sans" style={{ background: '#f8f7f4', color: '#1a1a2e' }}>
            <Header company={company} />
            <main className="flex-1">
                <div className="max-w-[1400px] mx-auto px-6 lg:px-12 py-10">
                    {children}
                </div>
            </main>
        </div>
    );
};
