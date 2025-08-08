import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function GithubCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get("code");

    if (code) {
      axios
        .post("http://localhost:8000/auth/github/", { code })
        .then((res) => {
          localStorage.setItem("access_token", res.data.access);
          localStorage.setItem("refresh_token", res.data.refresh);
          navigate("/dashboard");
        })
        .catch((err) => {
          console.error(err);
          alert("Login failed");
        });
    }
  }, [navigate]);

  return (
    <div className="container text-center mt-5">
      <h2>Logging you in...</h2>
    </div>
  );
}

export default GithubCallback;
