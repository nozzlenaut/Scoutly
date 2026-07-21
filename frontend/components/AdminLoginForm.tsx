export function AdminLoginForm({ next }: { next: string }) {
  return (
    <form method="post" action="/api/admin/session" className="mt-5 flex flex-col gap-3 sm:flex-row">
      <input type="hidden" name="next" value={next} />
      <label className="flex-1">
        <span className="sr-only">Admin token</span>
        <input
          name="token"
          type="password"
          required
          autoComplete="current-password"
          placeholder="Admin token"
          className="w-full rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/60"
        />
      </label>
      <button className="rounded-2xl bg-white px-5 py-3 font-semibold text-slate-950 transition hover:bg-slate-200">
        Open admin
      </button>
    </form>
  );
}

export function AdminLogoutButton() {
  return (
    <form method="post" action="/api/admin/logout">
      <button
        type="submit"
        className="w-fit rounded-2xl border border-white/10 px-5 py-3 font-bold text-slate-300 transition hover:bg-white/[0.08]"
      >
        Log out
      </button>
    </form>
  );
}
