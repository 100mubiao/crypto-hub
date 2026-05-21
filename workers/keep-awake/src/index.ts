const RENDER_HEALTH_URL = 'https://crypto-hub-api.onrender.com/api/v1/health';

export default {
	async scheduled(_event: ScheduledEvent, _env: Env, _ctx: ExecutionContext) {
		const resp = await fetch(RENDER_HEALTH_URL);
		if (!resp.ok) {
			throw new Error(`Health check failed: ${resp.status}`);
		}
		const body = await resp.text();
		console.log(`[keep-awake] ping success: ${body}`);
	},

	async fetch(_request: Request, _env: Env, _ctx: ExecutionContext) {
		const resp = await fetch(RENDER_HEALTH_URL);
		const body = await resp.text();
		return new Response(body, {
			headers: { 'content-type': 'application/json' },
		});
	},
} satisfies ExportedHandler<Env>;
