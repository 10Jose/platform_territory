import React, { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const RankingTable = () => {
  const [data, setData] = useState([]);
  const [sortField, setSortField] = useState("score");
  const [sortOrder, setSortOrder] = useState("desc");
  const [topFilter, setTopFilter] = useState("");
  const [orderFilter, setOrderFilter] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const fetchRanking = async () => {
    try {
      let url = `${API_URL}/api/ranking?order=${orderFilter}`;
      if (topFilter) url += `&top=${topFilter}`;
      const token = localStorage.getItem('token');
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const response = await fetch(url, { headers });
      const result = await response.json();
      setData(result.data || []);
      setCurrentPage(1);
    } catch (error) {
      console.error("Error fetching ranking:", error);
    }
  };

  useEffect(() => {
    fetchRanking();
  }, []);

  const handleApplyFilters = () => {
    fetchRanking();
  };

  const handleSort = (field) => {
    let order = "asc";
    if (sortField === field && sortOrder === "asc") order = "desc";
    setSortField(field);
    setSortOrder(order);
    const sorted = [...data].sort((a, b) => {
      let valA = a[field], valB = b[field];
      if (typeof valA === "string") { valA = valA.toLowerCase(); valB = valB.toLowerCase(); }
      if (valA < valB) return order === "asc" ? -1 : 1;
      if (valA > valB) return order === "asc" ? 1 : -1;
      return 0;
    });
    setData(sorted);
  };

  const getArrow = (field) => {
    if (sortField !== field) return "";
    return sortOrder === "asc" ? " 🔼" : " 🔽";
  };

  const totalPages = Math.ceil(data.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = data.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div style={{ padding: "30px", backgroundColor: "#f4f6f8" }}>
      <h2 style={{ marginBottom: "20px", color: "#0f172a" }}>📊 Ranking de Zonas</h2>

      {/* Filtros */}
      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
        <label style={{ fontSize: 14 }}>
          Top N:
          <input
            type="number" min="1" placeholder="Todos"
            value={topFilter} onChange={e => setTopFilter(e.target.value)}
            style={{ marginLeft: 6, width: 80, padding: "6px 8px", borderRadius: 6, border: "1px solid #d1d5db" }}
          />
        </label>
        <label style={{ fontSize: 14 }}>
          Orden:
          <select
            value={orderFilter} onChange={e => setOrderFilter(e.target.value)}
            style={{ marginLeft: 6, padding: "6px 8px", borderRadius: 6, border: "1px solid #d1d5db" }}
          >
            <option value="desc">Mayor a menor</option>
            <option value="asc">Menor a mayor</option>
          </select>
        </label>
        <button onClick={handleApplyFilters} style={{
          padding: "8px 16px", backgroundColor: "#0d9488", color: "white",
          border: "none", borderRadius: 8, cursor: "pointer", fontSize: 14,
        }}>
          Aplicar filtros
        </button>
      </div>

      <div style={{ backgroundColor: "white", borderRadius: "12px", boxShadow: "0 4px 12px rgba(0,0,0,0.1)", overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ backgroundColor: "#0d9488", color: "white", textAlign: "left" }}>
              <th style={thStyle} onClick={() => handleSort("rank")}>Posición{getArrow("rank")}</th>
              <th style={thStyle} onClick={() => handleSort("zone")}>Zona{getArrow("zone")}</th>
              <th style={thStyle} onClick={() => handleSort("score")}>Score{getArrow("score")}</th>
              <th style={thStyle} onClick={() => handleSort("level")}>Nivel{getArrow("level")}</th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((item, index) => (
              <tr
                key={item.rank}
                style={{ backgroundColor: index % 2 === 0 ? "#f9fafb" : "white", transition: "0.2s" }}
                onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#e0f2fe")}
                onMouseLeave={e => (e.currentTarget.style.backgroundColor = index % 2 === 0 ? "#f9fafb" : "white")}
              >
                <td style={tdStyle}>{item.rank}</td>
                <td style={tdStyle}>{item.zone}</td>
                <td style={tdStyle}>{item.score}</td>
                <td style={tdStyle}>{item.level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      {totalPages > 1 && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
          <span style={{ fontSize: 13, color: "#64748b" }}>
            Mostrando {startIndex + 1}-{Math.min(startIndex + itemsPerPage, data.length)} de {data.length}
          </span>
          <div style={{ display: "flex", gap: 4 }}>
            <button onClick={() => setCurrentPage(p => Math.max(p - 1, 1))} disabled={currentPage === 1} style={pageBtnStyle}>←</button>
            {[...Array(totalPages)].map((_, i) => (
              <button key={i} onClick={() => setCurrentPage(i + 1)}
                style={{ ...pageBtnStyle, backgroundColor: currentPage === i + 1 ? "#0d9488" : "white", color: currentPage === i + 1 ? "white" : "#333" }}>
                {i + 1}
              </button>
            ))}
            <button onClick={() => setCurrentPage(p => Math.min(p + 1, totalPages))} disabled={currentPage === totalPages} style={pageBtnStyle}>→</button>
          </div>
        </div>
      )}
    </div>
  );
};

const thStyle = { padding: "12px", cursor: "pointer" };
const tdStyle = { padding: "12px", borderBottom: "1px solid #e5e7eb" };
const pageBtnStyle = { padding: "6px 12px", border: "1px solid #d1d5db", borderRadius: 6, cursor: "pointer", fontSize: 13 };

export default RankingTable;
