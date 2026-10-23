// HomeTab component
function HomeTab({ levels }) {
  return (
    <div className="space-y-6">
      <div className="text-center border-b pb-4">
        <h2 className="text-2xl font-black tracking-widest text-black uppercase">RECENT VERIFICATION LEVEL</h2>
        <p className="text-sm font-semibold text-gray-500 uppercase tracking-widest">- IN ALL LIST -</p>
      </div>

      {/* Special Level Banner */}
      <div className="bg-gray-50 border-2 border-black p-4">
        <span className="bg-black text-white text-xs font-bold px-2 py-0.5 tracking-wider uppercase">SPECIAL MAIN LEVEL</span>
        <div className="mt-2 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold">FIH Cathedral (Main Server Level)</h3>
            <p className="text-xs text-gray-600">Hosted by PlayerLBM | Verified by Zoink | ID: 9948201</p>
          </div>
          <span className="text-sm font-mono font-bold bg-black text-white px-3 py-1">+500 PTS</span>
        </div>
      </div>

      {/* Level Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {levels.map((lvl) => (
          <div key={lvl.id} className="border-2 border-black p-4 bg-white flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="aspect-video bg-gray-200 border border-gray-400 mb-3 flex items-center justify-center relative overflow-hidden">
                <iframe className="w-full h-full" src={lvl.video} title={lvl.name} allowFullScreen></iframe>
              </div>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-lg">#{lvl.rank}</span>
                    <h4 className="font-bold text-lg">{lvl.name}</h4>
                  </div>
                  <p className="text-xs text-gray-600">By {lvl.creator} | Verified by {lvl.verifier}</p>
                </div>
                <span className="bg-gray-100 border border-gray-300 text-xs font-mono font-bold px-2 py-1">{lvl.difficulty}</span>
              </div>
            </div>
            <div className="border-t pt-2 mt-2 flex justify-between text-xs font-mono text-gray-500">
              <span>ID: {lvl.levelId}</span>
              <span className="font-bold text-black">+{lvl.points} PTS</span>
            </div>
          </div>
        ))}
      </div>

      {/* Ad Banner Placeholder */}
      <div className="border-2 border-dashed border-gray-400 p-4 text-center text-xs font-mono text-gray-400 uppercase tracking-widest">
        AD TAB - SPONSOR PLACEMENT
      </div>
    </div>
  );
}
