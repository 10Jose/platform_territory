import PropTypes from "prop-types";

function Ranking({ data }) {
    return (
        <div> 
            <h2>Ranking</h2>

            {data.map((item, index) => (
                <div key={index.id}>
                    <p>Zona: {item.zone}</p>
                    <p>Score: {item.score}</p>
                    <p>Nivel: {item.level}</p>
                </div>
                
            ))}
        </div>
    );
}
Ranking.propTypes = {
    data: PropTypes.array.isRequired
};

export default Ranking;
