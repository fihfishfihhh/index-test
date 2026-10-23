// CollabTab component
function CollabTab({ collabs, user, handleApplyCollab, handleApplicantStatus, showCollabModal, setShowCollabModal, newCollab, setNewCollab, handleCreateCollab }) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h2 className="text-xl font-bold uppercase">COLLAB HUB & HOST MANAGEMENT</h2>
          <p className="text-xs text-gray-500">Create, join, and manage GD megacollabs.</p>
        </div>
        <button onClick={() => setShowCollabModal(true)} className="bg-black text-white text-xs font-bold px-4 py-2 uppercase">
          + CREATE COLLAB
        </button>
      </div>

      {/* Active Collabs */}
      <div className="space-y-4">
        {collabs.map((collab) => {
          const isHost = collab.host === user.username;
          const myApp = collab.applicants.find(a => a.username === user.username);

          return (
            <div key={collab.id} className="border-2 border-black p-5 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-lg">{collab.title}</h3>
                    {isHost && <span className="bg-black text-white text-[10px] font-bold px-2 py-0.5">YOUR COLLAB</span>}
                  </div>
                  <p className="text-xs text-gray-600">Hosted by: <span className="font-bold">{collab.host}</span> | Difficulty: {collab.difficulty} | Deadline: {collab.deadline}</p>
                </div>

                {/* Join Action Button */}
                {!isHost && (
                  myApp ? (
                    <span className={`text-xs font-bold px-3 py-1 border ${
                      myApp.status === "Accepted" ? "bg-green-100 text-green-800 border-green-300" :
                      myApp.status === "Rejected" ? "bg-red-100 text-red-800 border-red-300" :
                      "bg-yellow-100 text-yellow-800 border-yellow-300"
                    }`}>
                      STATUS: {myApp.status.toUpperCase()}
                    </span>
                  ) : (
                    <button 
                      onClick={() => handleApplyCollab(collab.id)}
                      className="bg-black text-white text-xs font-bold px-4 py-2 uppercase hover:bg-gray-800 transition"
                    >
                      REQUEST TO JOIN
                    </button>
                  )
                )}
              </div>

              <p className="text-sm border-l-2 border-black pl-3 py-1 bg-gray-50">{collab.description}</p>

              {/* Slot Progress */}
              <div>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span>MEMBER SLOTS</span>
                  <span>{collab.slotsFilled} / {collab.slotsNeeded} SLOTS</span>
                </div>
                <div className="w-full bg-gray-200 h-2">
                  <div className="bg-black h-full" style={{ width: `${(collab.slotsFilled / collab.slotsNeeded) * 100}%` }}></div>
                </div>
              </div>

              {/* Host Dashboard Panel */}
              {isHost && collab.applicants.length > 0 && (
                <div className="bg-gray-100 border p-3 space-y-2">
                  <div className="text-xs font-bold uppercase">APPLICANT APPROVAL PANEL:</div>
                  {collab.applicants.map((app, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs bg-white p-2 border">
                      <span className="font-bold">{app.username}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500 font-mono">[{app.status}]</span>
                        {app.status === "Pending" && (
                          <>
                            <button onClick={() => handleApplicantStatus(collab.id, app.username, "Accepted")} className="bg-green-600 text-white font-bold px-2 py-1">ACCEPT</button>
                            <button onClick={() => handleApplicantStatus(collab.id, app.username, "Rejected")} className="bg-red-600 text-white font-bold px-2 py-1">REJECT</button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Modal Create Collab */}
      {showCollabModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white border-2 border-black p-6 w-full max-w-md space-y-4">
            <h3 className="text-lg font-bold uppercase border-b pb-2">HOST NEW COLLAB</h3>
            <form onSubmit={handleCreateCollab} className="space-y-3">
              <div>
                <label className="block text-xs font-bold mb-1">PROJECT TITLE</label>
                <input type="text" required className="w-full border p-2 text-sm" value={newCollab.title} onChange={e => setNewCollab({...newCollab, title: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">DESCRIPTION</label>
                <textarea required className="w-full border p-2 text-sm h-20" value={newCollab.description} onChange={e => setNewCollab({...newCollab, description: e.target.value})}></textarea>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-bold mb-1">TOTAL SLOTS</label>
                  <input type="number" min="2" max="20" required className="w-full border p-2 text-sm" value={newCollab.slotsNeeded} onChange={e => setNewCollab({...newCollab, slotsNeeded: parseInt(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-xs font-bold mb-1">TARGET DIFFICULTY</label>
                  <select className="w-full border p-2 text-sm" value={newCollab.difficulty} onChange={e => setNewCollab({...newCollab, difficulty: e.target.value})}>
                    <option>Hard Demon</option>
                    <option>Insane Demon</option>
                    <option>Extreme Demon</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold mb-1">DEADLINE</label>
                <input type="date" required className="w-full border p-2 text-sm" value={newCollab.deadline} onChange={e => setNewCollab({...newCollab, deadline: e.target.value})} />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowCollabModal(false)} className="px-4 py-2 text-xs border uppercase">CANCEL</button>
                <button type="submit" className="px-4 py-2 text-xs bg-black text-white font-bold uppercase">CREATE</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
