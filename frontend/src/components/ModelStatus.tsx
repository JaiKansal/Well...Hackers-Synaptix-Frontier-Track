import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ModelStatus.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ModelStatusData {
    is_trained: boolean;
    device: string;
    checkpoint_available: boolean;
    expected_sparsity: string;
    note: string;
}

const ModelStatus: React.FC = () => {
    const [status, setStatus] = useState<ModelStatusData | null>(null);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/model-status`);
                setStatus(response.data);
            } catch (error) {
                console.error('Failed to fetch model status:', error);
            }
        };

        fetchStatus();
        // Refresh status occasionally in case backend updates
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    if (!status) return null;

    return (
        <div className={`model-status-card ${status.is_trained ? 'trained' : 'random'}`}>
            <div className="status-icon">
                {status.is_trained ? '🎓' : '🎲'}
            </div>
            <div className="status-content">
                <div className="status-header">
                    <span className="status-title">
                        {status.is_trained ? 'Trained Model Active' : 'Demo Mode (Random)'}
                    </span>
                    <span className={`status-badge ${status.is_trained ? 'success' : 'warning'}`}>
                        {status.is_trained ? 'Optimal Performance' : 'Simulation Mode'}
                    </span>
                </div>
                <p className="status-note">{status.note}</p>
                <div className="status-details">
                    <span>Sparsity Target: <strong>{status.expected_sparsity}</strong></span>
                    <span className="separator">•</span>
                    <span>Device: <strong>{status.device}</strong></span>
                </div>
            </div>
        </div>
    );
};

export default ModelStatus;
