import React, { useEffect, useState } from "react";

const RankingTable = () => {
  const [data, setData] = useState([]);
  const [sortField, setSortField] = useState("score");
  const [sortOrder, setSortOrder] = useState("desc");

  const fetchRanking = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/ranking");
      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error("Error fetching ranking:", error);
    }
  };

  useEffect(() => {
    fetchRanking();
  }, []);

  const handleSort = (field) => {
    let order = "asc";

    if (sortField === field && sortOrder === "asc") {
      order = "desc";
    }

    setSortField(field);
    setSortOrder(order);

    const sorted = [...data].sort((a, b) => {
      let valA = a[field];
      let valB = b[field];

      if (typeof valA === "string") {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }

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

  return (
    <div style={{
      padding: "30px",
      backgroundColor: "#f4f6f8",
      minHeight: "100vh"
    }}>
      <h2 style={{
        marginBottom: "20px",
        color: "#0f172a"
      }}>
        📊 Ranking de Zonas
      </h2>

      <div style={{
        backgroundColor: "white",
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        overflow: "hidden"
      }}>
        <table style={{
          width: "100%",
          borderCollapse: "collapse"
        }}>
          <thead>
            <tr style={{
              backgroundColor: "#0d9488",
              color: "white",
              textAlign: "left"
            }}>
              <th style={thStyle} onClick={() => handleSort("rank")}>
                Posición{getArrow("rank")}
              </th>
              <th style={thStyle} onClick={() => handleSort("zone")}>
                Zona{getArrow("zone")}
              </th>
              <th style={thStyle} onClick={() => handleSort("score")}>
                Score{getArrow("score")}
              </th>
              <th style={thStyle} onClick={() => handleSort("level")}>
                Nivel{getArrow("level")}
              </th>
            </tr>
          </thead>

          <tbody>
            {data.map((item, index) => (
              <tr
                key={item.rank}
                style={{
                  backgroundColor: index % 2 === 0 ? "#f9fafb" : "white",
                  transition: "0.2s"
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.backgroundColor = "#e0f2fe")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.backgroundColor =
                    index % 2 === 0 ? "#f9fafb" : "white")
                }
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
    </div>
  );
};

// 🔥 estilos reutilizables
const thStyle = {
  padding: "12px",
  cursor: "pointer"
};

const tdStyle = {
  padding: "12px",
  borderBottom: "1px solid #e5e7eb"
};

export default RankingTable;