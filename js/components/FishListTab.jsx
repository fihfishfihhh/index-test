// FishListTab component
function FishListTab() {
  return (
    <div className="space-y-6">
      <div className="border-b pb-4">
        <h2 className="text-xl font-bold uppercase">FISH LIST - SPECIAL DEMON RANKINGS</h2>
        <p className="text-xs text-gray-500">Official FIH Server custom demon tier rankings.</p>
      </div>
      <div className="space-y-3">
        {[
          { rank: 1, name: "Fish Madness", creator: "FIH Team", points: 300 },
          { rank: 2, name: "Oceanic Nightmare", creator: "AquaDash", points: 270 }
        ].map(item => (
          <div key={item.rank} className="border p-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="font-black text-xl">#{item.rank}</span>
              <div>
                <div className="font-bold">{item.name}</div>
                <div className="text-xs text-gray-500">By {item.creator}</div>
              </div>
            </div>
            <span className="font-mono text-xs font-bold border px-3 py-1">{item.points} PTS</span>
          </div>
        ))}
      </div>
    </div>
  );
}
