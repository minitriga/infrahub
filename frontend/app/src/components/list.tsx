import { forwardRef, useState } from "react";
import { toast } from "react-toastify";

import { ALERT_TYPES, Alert } from "@/components/ui/alert";
import { FormFieldError } from "@/screens/edit-form-hook/form";
import { Input } from "./inputs/input";
import { MultipleInput } from "./inputs/multiple-input";
import { SelectOption } from "./inputs/select";

type OpsListProps = {
  id?: string;
  value: (string | SelectOption)[];
  onChange: (value: (string | SelectOption)[]) => void;
  error?: FormFieldError;
  isProtected?: boolean;
  disabled?: boolean;
};

const List = forwardRef<HTMLInputElement, OpsListProps>((props, ref) => {
  const { value = [], onChange, id, error, isProtected, disabled } = props;

  const [inputValue, sertInputValue] = useState("");

  const handleInputChange = (newValue: string) => {
    sertInputValue(newValue);
  };

  const handleKeyDown = (event: any) => {
    if (event.key === "Enter") {
      // Prevent default behaviour
      event.preventDefault();
      event.stopPropagation();

      // Build new array with unique items
      const newArray = Array.from(new Set([...(value || []), inputValue]));

      onChange(newArray);

      // Init input
      sertInputValue("");

      if (newArray.length === value.length) {
        toast(<Alert message="Item already in the list" type={ALERT_TYPES.INFO} />);
      }
    }
  };

  return (
    <div>
      <Input
        ref={ref}
        id={id}
        onChange={handleInputChange}
        error={error}
        disabled={isProtected}
        placeholder="Add a new item + hit 'enter'"
        className="mb-1"
        onKeyDown={handleKeyDown}
        value={inputValue}
      />
      <MultipleInput value={value} onChange={onChange} disabled={disabled} />
    </div>
  );
});

export default List;
