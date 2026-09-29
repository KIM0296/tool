import { site } from "@/content/site";

function isExternal(href: string) {
  return href.startsWith("http");
}

function LinkButton({
  href,
  label,
  variant = "primary",
}: {
  href: string;
  label: string;
  variant?: "primary" | "secondary";
}) {
  return (
    <a
      className={`btn btn-${variant}`}
      href={href}
      {...(isExternal(href) ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    >
      {label}
    </a>
  );
}

export default function Home() {
  const { cta, hero } = site;

  return (
    <>
      <header className="nav">
        <div className="container nav-inner">
          <a href="#" className="logo">
            {site.name}
          </a>
          <nav className="nav-links">
            <a href="#features">기능</a>
            <a href="#how">사용 방법</a>
            <a href="#pricing">요금제</a>
            <a href="#faq">FAQ</a>
          </nav>
          <LinkButton href={cta.primaryHref} label={cta.primaryLabel} />
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container hero-inner">
            <span className="badge">{hero.badge}</span>
            <h1>{hero.headline}</h1>
            <p className="lead">{hero.subheadline}</p>
            <div className="cta-row">
              <LinkButton href={cta.primaryHref} label={cta.primaryLabel} />
              <LinkButton href={cta.secondaryHref} label={cta.secondaryLabel} variant="secondary" />
            </div>
            <p className="note">{hero.note}</p>

            <ul className="stats">
              {site.stats.map((s) => (
                <li key={s.label}>
                  <strong>{s.value}</strong>
                  <span>{s.label}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section id="features" className="section">
          <div className="container">
            <h2 className="section-title">필요한 기능을 모두 담았습니다</h2>
            <div className="grid-3">
              {site.features.map((f) => (
                <article key={f.title} className="card">
                  <div className="card-icon" aria-hidden>
                    {f.icon}
                  </div>
                  <h3>{f.title}</h3>
                  <p>{f.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="how" className="section section-alt">
          <div className="container">
            <h2 className="section-title">3단계면 시작할 수 있어요</h2>
            <ol className="steps">
              {site.steps.map((s, i) => (
                <li key={s.title}>
                  <span className="step-num">{i + 1}</span>
                  <h3>{s.title}</h3>
                  <p>{s.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section id="pricing" className="section">
          <div className="container">
            <h2 className="section-title">나에게 맞는 요금제를 고르세요</h2>
            <div className="grid-3">
              {site.pricing.map((p) => (
                <article key={p.name} className={`card price${p.highlighted ? " price-hl" : ""}`}>
                  {p.highlighted && <span className="badge">가장 인기</span>}
                  <h3>{p.name}</h3>
                  <p className="price-amount">
                    {p.price}
                    <span>{p.period}</span>
                  </p>
                  <ul className="checklist">
                    {p.features.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                  <LinkButton
                    href={p.ctaHref}
                    label={p.ctaLabel}
                    variant={p.highlighted ? "primary" : "secondary"}
                  />
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="faq" className="section section-alt">
          <div className="container narrow">
            <h2 className="section-title">자주 묻는 질문</h2>
            {site.faq.map((item) => (
              <details key={item.q} className="faq-item">
                <summary>{item.q}</summary>
                <p>{item.a}</p>
              </details>
            ))}
          </div>
        </section>

        <section className="final-cta">
          <div className="container narrow">
            <h2>{site.finalCta.headline}</h2>
            <p>{site.finalCta.body}</p>
            <LinkButton href={cta.primaryHref} label={cta.primaryLabel} />
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container footer-inner">
          <span>{site.footer.company}</span>
          <nav>
            {site.footer.links.map((l) => (
              <a key={l.label} href={l.href}>
                {l.label}
              </a>
            ))}
          </nav>
        </div>
      </footer>
    </>
  );
}
