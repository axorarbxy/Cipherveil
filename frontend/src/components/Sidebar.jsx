function Sidebar({ currentPage, setCurrentPage }) {

  const menuItems = [
    {
      id: "dashboard",
      icon: "🏠",
      label: "Dashboard"
    },
    {
      id: "events",
      icon: "📊",
      label: "Live Events"
    },
    {
      id: "simulation",
      icon: "🧪",
      label: "Simulation"
    },
    {
      id: "alerts",
      icon: "🚨",
      label: "Alerts"
    },
    {
      id: "history",
      icon: "📜",
      label: "Incident History"
    },
    {
      id: "reports",
      icon: "📄",
      label: "Incident Reports"
    }
  ];

  return (
    <aside className="sidebar">

      {/* Logo / Project Name */}

      <div className="sidebar-brand">

        <div className="brand-icon">
          🛡️
        </div>

        <div>
          <h1>CYB04</h1>

          <p>
            Ransomware Early-Warning
          </p>
        </div>

      </div>


      {/* Navigation */}

      <nav className="sidebar-nav">

        {menuItems.map((item) => (

          <button
            key={item.id}
            className={`nav-item ${
              currentPage === item.id ? "active" : ""
            }`}
            onClick={() => setCurrentPage(item.id)}
          >

            <span className="nav-icon">
              {item.icon}
            </span>

            <span>
              {item.label}
            </span>

          </button>

        ))}

      </nav>

    </aside>
  );
}

export default Sidebar;