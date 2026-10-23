// Main App: owns all state and handlers, composes the components.
const { useState } = React;

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("ALL");

  // User session state
  const [user] = useState(INITIAL_USER);

  // Data states
  const [levels] = useState(INITIAL_DEMON_LIST);
  const [collabs, setCollabs] = useState(INITIAL_COLLABS);
  const [submissions, setSubmissions] = useState([]);
  const [helpers] = useState(INITIAL_HELPERS);

  // Form modals
  const [showCollabModal, setShowCollabModal] = useState(false);
  const [newCollab, setNewCollab] = useState({ title: "", description: "", slotsNeeded: 4, difficulty: "Insane Demon", deadline: "" });

  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [newSubmission, setNewSubmission] = useState({ levelName: "", levelId: "", creator: "", videoUrl: "" });

  // Apply to a collab
  const handleApplyCollab = (collabId) => {
    setCollabs(collabs.map(c => {
      if (c.id === collabId) {
        const alreadyApplied = c.applicants.some(a => a.username === user.username);
        if (!alreadyApplied) {
          return { ...c, applicants: [...c.applicants, { username: user.username, status: "Pending" }] };
        }
      }
      return c;
    }));
  };

  // Approve / reject an applicant
  const handleApplicantStatus = (collabId, username, status) => {
    setCollabs(collabs.map(c => {
      if (c.id === collabId) {
        const updatedApplicants = c.applicants.map(a => a.username === username ? { ...a, status } : a);
        const acceptedCount = updatedApplicants.filter(a => a.status === "Accepted").length;
        return { ...c, applicants: updatedApplicants, slotsFilled: Math.min(c.slotsNeeded, acceptedCount + 1) };
      }
      return c;
    }));
  };

  // Create a new collab
  const handleCreateCollab = (e) => {
    e.preventDefault();
    if (!newCollab.title) return;
    const item = {
      id: Date.now(),
      ...newCollab,
      host: user.username,
      slotsFilled: 1,
      applicants: []
    };
    setCollabs([item, ...collabs]);
    setShowCollabModal(false);
    setNewCollab({ title: "", description: "", slotsNeeded: 4, difficulty: "Insane Demon", deadline: "" });
  };

  // Create a new level submission
  const handleCreateSubmission = (e) => {
    e.preventDefault();
    if (!newSubmission.levelName) return;
    setSubmissions([{ id: Date.now(), ...newSubmission, status: "Under Review", date: new Date().toLocaleDateString() }, ...submissions]);
    setShowSubmitModal(false);
    setNewSubmission({ levelName: "", levelId: "", creator: "", videoUrl: "" });
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        searchCategory={searchCategory}
        setSearchCategory={setSearchCategory}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        user={user}
      />

      <div className="flex flex-1">
        {sidebarOpen && (
          <Sidebar user={user} activeTab={activeTab} setActiveTab={setActiveTab} />
        )}

        <main className="flex-1 bg-white p-6 overflow-y-auto">
          {activeTab === "home" && <HomeTab levels={levels} />}
          {activeTab === "discord" && <DiscordTab />}
          {activeTab === "submit" && (
            <SubmitTab
              submissions={submissions}
              showSubmitModal={showSubmitModal}
              setShowSubmitModal={setShowSubmitModal}
              newSubmission={newSubmission}
              setNewSubmission={setNewSubmission}
              handleCreateSubmission={handleCreateSubmission}
            />
          )}
          {activeTab === "creators" && <CreatorsTab />}
          {activeTab === "collab" && (
            <CollabTab
              collabs={collabs}
              user={user}
              handleApplyCollab={handleApplyCollab}
              handleApplicantStatus={handleApplicantStatus}
              showCollabModal={showCollabModal}
              setShowCollabModal={setShowCollabModal}
              newCollab={newCollab}
              setNewCollab={setNewCollab}
              handleCreateCollab={handleCreateCollab}
            />
          )}
          {activeTab === "helpers" && <HelpersTab helpers={helpers} />}
          {activeTab === "fishlist" && <FishListTab />}
          {activeTab === "otherlist" && <OtherListTab />}
        </main>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
