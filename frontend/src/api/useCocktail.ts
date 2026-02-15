import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import type { Cocktail } from '../types';

export default function useCocktail(name?: string) {
  return useQuery({
    staleTime: 60 * 1000, // 1 minute
    queryKey: ['cocktails', name],
    queryFn: async () => {
      if (!name) {
        return null;
      }

      const response = await apiClient.get<Cocktail>(
        `/cocktails/${encodeURIComponent(name)}`
      );
      return {
        ...response.data,
        can_make: response.data.is_available ?? response.data.can_make,
      };
    },
    enabled: !!name,
  });
}
