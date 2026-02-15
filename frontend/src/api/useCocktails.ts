import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import type { Cocktail } from '../types';

export default function useCocktails() {
  return useQuery({
    staleTime: 60 * 1000, // 1 minute
    queryKey: ['cocktails'],
    queryFn: async () => {
      const response = await apiClient.get<Cocktail[]>('/cocktails');

      // Map is_available to can_make for backward compatibility
      return response.data.map((c) => ({
        ...c,
        can_make: c.is_available ?? c.can_make,
      }));
    },
  });
}
