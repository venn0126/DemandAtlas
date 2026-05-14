import { NavLink, Outlet } from 'react-router-dom'

import { useI18n } from '../../i18n/use-i18n'
import { routes } from '../../app/routes'

export function AppShell() {
  const { t } = useI18n()
  const navItems = [
    { to: routes.home, label: t('nav.home') },
    { to: routes.oneClick, label: t('nav.oneClick') },
    { to: routes.directed, label: t('nav.directed') },
    { to: routes.settings, label: t('nav.settings') },
  ]

  return (
    <div className="app-shell">
      <header className="top-nav">
        <div className="brand-block">
          <div className="brand-mark">DA</div>
          <div>
            <p className="brand-title">{t('brand.title')}</p>
            <p className="brand-subtitle">{t('brand.subtitle')}</p>
          </div>
        </div>

        <nav className="top-nav-links" aria-label={t('nav.mainNavigation')}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? 'top-nav-link top-nav-link-active' : 'top-nav-link'
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="page-main">
        <Outlet />
      </main>
    </div>
  )
}
