import { format, formatDistanceStrict, formatDistanceToNow } from "date-fns";
import { Tooltip } from "../utils/tooltip";

type DateDisplayProps = {
  date?: number | string | Date;
  endDate?: number | string | Date;
  hideDefault?: boolean;
};

export const getDateDisplay = (date?: number | string | Date) =>
  format(date ? new Date(date) : new Date(), "yyyy-MM-dd HH:mm:ss (O)");

export const DateDisplay = (props: DateDisplayProps) => {
  const { date, endDate, hideDefault } = props;

  if (!date && hideDefault) {
    return null;
  }

  // Display duration
  if (endDate) {
    const tooltip = `${getDateDisplay(date)} -> ${getDateDisplay(endDate)}`;

    return (
      <span className="flex items-center flex-wrap">
        <Tooltip message={tooltip}>
          <span className="text-xs font-normal">
            {formatDistanceStrict(
              date ? new Date(date) : new Date(),
              endDate ? new Date(endDate) : new Date()
            )}
          </span>
        </Tooltip>
      </span>
    );
  }

  return (
    <span className="flex items-center flex-wrap">
      <Tooltip message={getDateDisplay(date)}>
        <span className="text-xs font-normal">
          {formatDistanceToNow(date ? new Date(date) : new Date(), { addSuffix: true })}
        </span>
      </Tooltip>
    </span>
  );
};
