import PropTypes from 'prop-types';

function Indicators({ data = [] }) {
    return (
        <div>
            <h2>Indicadores</h2>

            {data.map((item, index) => (
                <div key={item?.id ?? index}>
                    <p>Zona: {item.zone_name}</p>
                    <p>Población: {item.population_indicator}</p>
                    <p>Ingreso: {item.income_indicator}</p>
                </div>
            ))}
        </div>
        );
}
Indicators.propTypes = {
    data: PropTypes.array.isRequired
};
export default Indicators;