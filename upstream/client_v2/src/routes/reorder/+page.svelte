<script lang="ts">
	import { onMount } from 'svelte';
	import Card from '$components/Card.svelte';
	import { getReorderPlan, type ReorderItem } from '$lib/api/reorder';
	import { getSettings, parseSetting, setSetting } from '$lib/api/settings';

	let items = $state<ReorderItem[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let baseUrl = $state('');
	let providerVariants = $state<Record<string, string>>({});
	let saveMessage = $state('');

	onMount(() => {
		const controller = new AbortController();
		Promise.all([getReorderPlan(controller.signal), getSettings(controller.signal)])
			.then(([value, allSettings]) => {
				items = value;
				const provider = parseSetting(allSettings.reorder_providers, { base_url: '', variants: {} });
				baseUrl = provider.base_url ?? '';
				providerVariants = { ...(provider.variants ?? {}) };
			})
			.catch((e) => {
				if (!controller.signal.aborted) error = e instanceof Error ? e.message : 'Unable to load reorder plan';
			})
			.finally(() => (loading = false));
		return () => controller.abort();
	});

	async function saveProvider() {
		saveMessage = '';
		await setSetting('reorder_providers', { base_url: baseUrl.trim(), variants: providerVariants });
		saveMessage = 'Saved. Reload the plan to validate links.';
	}
</script>

<svelte:head><title>Reorder</title></svelte:head>

<div class="page scroll-y">
	<div class="wrap">
		<div class="title">Reorder</div>
		<p class="intro">Items below the configured stock policy. This view never changes inventory.</p>
		<Card>
			<label>Shop base URL <input bind:value={baseUrl} placeholder="https://eu.store.bambulab.com" /></label>
			<p class="hint">Variant IDs must be verified manually. No login or current shop cart is accessed.</p>
		</Card>

		{#if loading}
			<Card><p class="muted">Loading reorder plan…</p></Card>
		{:else if error}
			<Card><p class="error">{error}</p></Card>
		{:else if items.length === 0}
			<Card><p class="muted">No reorder is currently required.</p></Card>
		{:else}
			<div class="grid">
				{#each items as item (item.profile)}
					<Card>
						<div class="profile">{item.profile}</div>
						<div class="facts">
							<span>{item.remaining_g.toFixed(0)} g remaining</span>
							<span>{item.unopened} unopened</span>
						</div>
						<div class="order">Suggested quantity: <strong>{item.order_qty}</strong></div>
						<label class="variant">Verified Shopify variant ID
							<input bind:value={providerVariants[item.profile]} inputmode="numeric" placeholder="e.g. 123456789" />
						</label>
						{#if item.cart_url}
							<a class="cart" href={item.cart_url} target="_blank" rel="noopener noreferrer">Open prepared cart</a>
						{:else}
							<p class="warning">No verified shop variant is configured.</p>
						{/if}
					</Card>
				{/each}
			</div>
		{/if}
		<button class="save" onclick={saveProvider}>Save provider mapping</button>
		{#if saveMessage}<span class="saved">{saveMessage}</span>{/if}
	</div>
</div>

<style>
	.wrap { width: min(1100px, 100%); margin: 0 auto; padding: 28px; }
	.title { font-size: 1.7rem; font-weight: 700; margin-bottom: 8px; }
	.intro, .muted { color: var(--text-muted); }
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
	.profile { font-weight: 650; line-height: 1.35; }
	.facts { display: flex; gap: 16px; margin: 18px 0 10px; color: var(--text-muted); font-size: .92rem; }
	.order { margin-top: 8px; }
	.warning { margin: 16px 0 0; color: var(--warning, #a45a00); font-size: .88rem; }
	label { display: flex; flex-direction: column; gap: 6px; font-size: .9rem; }
	input { border: 1px solid var(--border-strong); border-radius: var(--radius-md); background: var(--surface); color: var(--text); padding: 9px 10px; }
	.variant { margin-top: 16px; }
	.hint, .saved { color: var(--text-muted); font-size: .85rem; }
	.save, .cart { display: inline-block; margin-top: 18px; padding: 9px 13px; border-radius: var(--radius-md); border: 0; background: var(--accent-fill); color: white; cursor: pointer; text-decoration: none; }
	.cart { background: var(--accent); }
	.error { color: var(--danger, #b42318); }
	@media (max-width: 600px) { .wrap { padding: 20px 16px; } .facts { flex-direction: column; gap: 4px; } }
</style>

