import { Footer } from "./components/Footer";
import { GenerateButton } from "./components/GenerateButton";
import { Navbar } from "./components/Navbar";
import { StatusAlert } from "./components/StatusAlert";
import { ZipDropzone } from "./components/ZipDropzone";
import { useFiscalUpload } from "./hooks/useFiscalUpload";
import "./App.css";

export function App() {
  const {
    files,
    isLoading,
    errorMsg,
    successMsg,
    remainingSlots,
    isFull,
    addFiles,
    removeFile,
    submitReports,
  } = useFiscalUpload();

  return (
    <div className="app-layout">
      <Navbar />

      <main className="main-container">
        <div className="panel-header">
          <h1>Painel de Geração de Arquivos Fiscais</h1>
          <p>Envie de 1 a 3 lotes (.zip) com XMLs fiscais para gerar os relatórios em PDF</p>
        </div>

        <section className="panel-body">
          <ZipDropzone
            files={files}
            isFull={isFull}
            disabled={isLoading}
            remainingSlots={remainingSlots}
            onFilesAdded={addFiles}
            onRemoveFile={removeFile}
          />

          <StatusAlert type="error" message={errorMsg} />
          <StatusAlert type="success" message={successMsg} />

          <GenerateButton
            isLoading={isLoading}
            disabled={files.length === 0}
            onClick={submitReports}
          />
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default App;