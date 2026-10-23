// CreatorsTab component
function CreatorsTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold uppercase border-b pb-4">FIH VERIFIED CREATORS</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { name: "PlayerLBM", title: "Host / Level Architect", points: 2450, featured: "Cathedral" },
          { name: "AquaDash", title: "Glow & Effects Specialist", points: 1890, featured: "Sunset Breeze" },
          { name: "VortXX", title: "Layout Designer", points: 1320, featured: "Cybernetics Part 1" }
        ].map((c, i) => (
          <div key={i} className="border-2 border-black p-4 space-y-2">
            <div className="font-bold text-base">{c.name}</div>
            <div className="text-xs text-gray-500 font-mono">{c.title}</div>
            <div className="text-xs bg-gray-100 p-2 border">Featured Work: <span className="font-bold">{c.featured}</span></div>
            <div className="text-right text-xs font-mono font-bold">{c.points} CREATOR PTS</div>
          </div>
        ))}
      </div>
    </div>
  );
}
