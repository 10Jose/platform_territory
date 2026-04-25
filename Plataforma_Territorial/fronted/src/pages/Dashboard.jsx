import { useEffect, useState } from "react";
import { api } from "../services/api";
import Ranking from "../components/Ranking";
import Indicators from "../components/Indicators";

function Dashboard() {
    const [ranking, setRanking] = useState([]);
    const [indicators, setIndicators] = useState([]);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        const rankingres = await api.getRanking();
        const indicatorsRes = await api.getIndicators();

        setRanking(rankingres.data);
        setIndicators(indicatorsRes.data);
    };

    return (
        <div>
            <h1>Dashboard Analitico</h1>

            <Indicators data={indicators}/>
            <Ranking data={ranking}/>
        </div>
    )
}
export default Dashboard;