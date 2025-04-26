%% Used To compute the MCS Area In a room
% Assumes room is a square
% Assumes MCS region is a circle 

function area = compute_area(d_max,room_radius)
    Area_circle = (pi) * d_max^2;
    area = 0;
        if(2*d_max >= room_radius*2*sqrt(2))
        area = (room_radius*2)^2;
        return
    end
    if d_max > (room_radius) %Divide by two because the AP is in the center, and d_max is radius. 
        room_radius = room_radius ;
        x_2 = sqrt(d_max^2 - room_radius^2);
        x_1 = -1 * x_2;
        temp1 = asin(x_2/d_max) + ((sin(2*asin(x_2/d_max))) / 2);
        temp2 = asin(x_1/d_max) + ((sin(2*asin(x_1/d_max))) / 2);
        I = ((d_max^2)/2) * (temp1 - temp2);
        I = I - ((room_radius) * (x_2 - x_1));
        I = I *4;
        area = Area_circle - I;
    else
        area = Area_circle;
    end
end

