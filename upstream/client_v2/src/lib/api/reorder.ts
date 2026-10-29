import { getJson } from './http';

export interface ReorderItem {
	profile: string;
	filament_id: number;
	remaining_g: number;
	unopened: number;
	order_qty: number;
	variant_id: string | null;
	cart_url: string | null;
}

export function getReorderPlan(signal?: AbortSignal): Promise<ReorderItem[]> {
	return getJson<ReorderItem[]>('/reorder', {}, signal);
}

