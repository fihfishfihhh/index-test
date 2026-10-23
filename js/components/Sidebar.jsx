// Sidebar component
function Sidebar({ user, activeTab, setActiveTab }) {
  return (
    <aside className="w-64 bg-black text-white flex flex-col justify-between p-4 border-r border-gray-800">
      <div>
        {/* User Profile Card */}
        <div className="bg-gray-900 border border-gray-800 p-3 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white text-black font-extrabold flex items-center justify-center text-sm rounded-full">
              PFP
            </div>
            <div>
              <div className="font-bold text-sm tracking-wide">{user.username}</div>
              <div className="text-xs text-gray-400">{user.achievement}</div>
            </div>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs font-mono mb-1">
              <span>POINT</span>
              <span>{user.points} / {user.maxPoints}</span>
            </div>
            <div className="w-full bg-gray-800 h-2 rounded overflow-hidden">
              <div className="bg-white h-full" style={{ width: `${(user.points / user.maxPoints) * 100}%` }}></div>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {[
            { id: "home", label: "HOME" },
            { id: "discord", label: "JOIN DISCORD" },
            { id: "submit", label: "SUBMIT LEVEL" },
            { id: "creators", label: "CREATOR LIST" },
            { id: "collab", label: "COLLAB HOST" },
            { id: "helpers", label: "FIND HELPER" },
            { id: "fishlist", label: "FISH LIST" },
            { id: "otherlist", label: "OTHER LIST" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full text-left px-3 py-2 text-sm font-semibold tracking-wider transition border-l-2 ${
                activeTab === tab.id
                  ? "bg-white text-black border-black font-bold"
                  : "text-gray-300 border-transparent hover:bg-gray-900 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="text-xs text-gray-500 font-mono text-center pt-4 border-t border-gray-800">
        FIH COMMUNITY v1.0
      </div>
    </aside>
  );
}
