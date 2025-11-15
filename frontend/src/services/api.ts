import axios from 'axios';
import { Cocktail, SystemStatus, MakeCocktailRequest } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    getCocktails: async (): Promise<Cocktail[]> => {
        const response = await apiClient.get<Cocktail[]>('/cocktails');
        // Map is_available to can_make for backward compatibility
        return response.data.map(c => ({ ...c, can_make: c.is_available ?? c.can_make }));
    },

    getAvailableCocktails: async (): Promise<Cocktail[]> => {
        const response = await apiClient.get<Cocktail[]>('/cocktails/available');
        return response.data.map(c => ({ ...c, can_make: c.is_available ?? c.can_make }));
    },

    getCocktail: async (name: string): Promise<Cocktail> => {
        const response = await apiClient.get<Cocktail>(`/cocktails/${encodeURIComponent(name)}`);
        return response.data;
    },

    makeCocktail: async (name: string, sizeMl: number): Promise<void> => {
        const request: MakeCocktailRequest = { size_ml: sizeMl };
        await apiClient.post(`/cocktails/${encodeURIComponent(name)}/make`, request);
    },

    getStatus: async (): Promise<SystemStatus> => {
        const response = await apiClient.get<SystemStatus>('/status');
        return response.data;
    },

    cancelMixing: async (): Promise<void> => {
        await apiClient.post('/status/cancel');
    },

    stopMixing: async (): Promise<void> => {
        await apiClient.post('/status/stop');
    },
};
