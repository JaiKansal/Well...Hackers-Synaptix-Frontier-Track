/**
 * Custom React hooks for BDH Brain Explorer
 */

import { useState, useEffect, useCallback } from 'react';
import {
    runInference,
    getTopology,
    measureSparsity,
    getConfig,
    InferenceRequest,
    InferenceResponse,
    TopologyResponse,
    SparsityMetrics,
} from '../utils/api';

/**
 * Hook for BDH inference
 */
export const useBDHInference = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<InferenceResponse | null>(null);

    const infer = useCallback(async (request: InferenceRequest) => {
        setLoading(true);
        setError(null);
        try {
            const result = await runInference(request);
            setData(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Inference failed';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { infer, loading, error, data };
};

/**
 * Hook for graph topology
 */
export const useTopology = (threshold: number = 0.1, topKNodes?: number) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<TopologyResponse | null>(null);

    const fetchTopology = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await getTopology(threshold, topKNodes);
            setData(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to fetch topology';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [threshold, topKNodes]);

    useEffect(() => {
        fetchTopology();
    }, [fetchTopology]);

    return { data, loading, error, refetch: fetchTopology };
};

/**
 * Hook for sparsity measurement
 */
export const useSparsity = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<SparsityMetrics | null>(null);

    const measure = useCallback(async (request: InferenceRequest) => {
        setLoading(true);
        setError(null);
        try {
            const result = await measureSparsity(request);
            setData(result);
            return result;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Sparsity measurement failed';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    return { measure, loading, error, data };
};

/**
 * Hook for model configuration
 */
export const useModelConfig = () => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [config, setConfig] = useState<any>(null);

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const result = await getConfig();
                setConfig(result);
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Failed to fetch config';
                setError(message);
            } finally {
                setLoading(false);
            }
        };

        fetchConfig();
    }, []);

    return { config, loading, error };
};