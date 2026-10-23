// Header component
function Header({ sidebarOpen, setSidebarOpen, searchCategory, setSearchCategory, searchQuery, setSearchQuery, user }) {
  return (
    <header className="bg-black text-white px-6 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="bg-white text-black text-xs font-bold px-3 py-1.5 uppercase hover:bg-gray-200 transition"
        >
          {sidebarOpen ? "HIDE TAB" : "SHOW TAB"}
        </button>
        <h1 className="text-xl font-extrabold tracking-wider">FIH COMMUNITY</h1>
      </div>

      {/* Top Search Bar */}
      <div className="flex items-center bg-gray-900 border border-gray-700 px-3 py-1 rounded w-1/2">
        <span className="text-xs text-gray-400 font-mono mr-2">SEARCH :</span>
        <div className="flex text-xs font-semibold gap-2 mr-3 border-r border-gray-700 pr-3">
          {["ALL", "PLAYER", "LEVEL", "LIST", "COLAB"].map(cat => (
            <button 
              key={cat}
              onClick={() => setSearchCategory(cat)}
              className={`hover:text-white transition ${searchCategory === cat ? "text-white underline" : "text-gray-400"}`}
            >
              {cat}
            </button>
          ))}
        </div>
        <input 
          type="text" 
          placeholder="Type here to search..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-transparent text-white text-sm outline-none w-full"
        />
      </div>

      {/* User Quick Info */}
      <div className="text-xs text-right font-mono">
        <div className="font-bold text-gray-200">{user.username}</div>
        <div className="text-green-400">{user.points} PT</div>
      </div>
    </header>
  );
}
