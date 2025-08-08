import { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    axios
      .get("http://localhost:8000/api/user/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      .then((res) => setUser(res.data))
      .catch((err) => console.error("Error:", err));
  }, []);

  return (
    <div className="container mt-5">
      <h1>Dashboard</h1>
      <p>Logged in as: {user?.username || "Loading..."}</p>
    </div>
  );
}

export default Dashboard;
