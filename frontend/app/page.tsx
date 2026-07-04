import Chat from "@/components/chat";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-1 items-stretch bg-ink p-3 sm:p-5">
      <div className="flex w-full flex-col rounded-[2.5rem] border-2 border-accent bg-white px-4 pb-8 pt-4 sm:px-8">
        {/* Nav */}
        <header className="flex items-center justify-between rounded-full bg-ink px-6 py-4 sm:px-8">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-full border border-accent/60 text-accent">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 10.5 12 3l9 7.5" />
                <path d="M5 9.5V21h14V9.5" />
                <path d="M9 21v-6h6v6" />
              </svg>
            </span>
            <div className="leading-tight">
              <p className="text-sm font-medium tracking-wide text-white">
                Casa Atardecer
              </p>
              <p className="text-[10px] uppercase tracking-[0.2em] text-accent">
                Concierge
              </p>
            </div>
          </div>

          <nav className="hidden items-center gap-8 text-sm text-neutral-300 md:flex">
            <a href="#" className="transition hover:text-white">
              Inicio
            </a>
            <a href="#" className="transition hover:text-white">
              La Casa
            </a>
            <a href="#" className="transition hover:text-white">
              Servicios
            </a>
            <a href="#concierge" className="transition hover:text-white">
              Concierge
            </a>
          </nav>

          <a
            href="#concierge"
            className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-ink transition hover:bg-accent-dark"
          >
            Hablar ahora
          </a>
        </header>

        {/* Hero + Chat */}
        <main className="mx-auto grid w-full max-w-6xl flex-1 items-center gap-12 py-12 lg:grid-cols-[1.1fr_1fr] lg:gap-16 lg:py-16">
          <section>
            <h1 className="font-display text-5xl leading-[1.05] tracking-wide text-ink sm:text-6xl xl:text-7xl">
              TU ESTANCIA
              <br />
              PERFECTA
              <br />
              <span className="text-accent">EMPIEZA AQUÍ</span>
            </h1>

            <p className="mt-8 max-w-md text-base font-light leading-relaxed text-neutral-500">
              Descubre Casa Atardecer con la ayuda de tu concierge personal.
              Consulta la ubicación, revisa disponibilidad en el calendario y
              resuelve cualquier duda sobre tu estancia, en tiempo real.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-6">
              <a
                href="#concierge"
                className="rounded-full bg-ink px-8 py-4 text-sm font-medium tracking-wide text-white transition hover:bg-neutral-800"
              >
                Preguntar al concierge
              </a>
              <div className="flex items-center gap-3 text-sm text-neutral-500">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-white">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 3v13" />
                    <path d="M6 12l6 6 6-6" />
                  </svg>
                </span>
                Atención inmediata, 24/7
              </div>
            </div>
          </section>

          <section id="concierge" className="scroll-mt-8">
            <Chat />
          </section>
        </main>
      </div>
    </div>
  );
}
