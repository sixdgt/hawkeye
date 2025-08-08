import Login from "./components/Login";

function App() {
  return (
    <div className="container text-center mt-5">
      <Login />
      <h1>Hawkeye</h1>
      <p>Welcome to the Hawkeye application!</p>
      <p>Login with GitHub to get started.</p>
      <footer className="mt-5">
        <p>&copy; {new Date().getFullYear()} Hawkeye Team</p>
      </footer>
    </div>
  );
}

export default App;
